#!/usr/bin/env python3
"""
Cold Outreach Automation System for Personal Training Business
Main orchestration script that coordinates email and SMS outreach.
"""

import sys
import time
import argparse
from datetime import datetime
from typing import Dict, List

# Service imports
from services.sheets_service import SheetsService
from services.email_service import EmailService
from services.sms_service import SMSService

# Utility imports
from config import config
from utils.logger import logger, log_operation, log_error

class OutreachAutomation:
    """Main automation orchestrator."""
    
    def __init__(self):
        self.sheets_service = None
        self.email_service = None
        self.sms_service = None
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all required services."""
        try:
            logger.info("Initializing Outreach Automation System")
            
            # Initialize services
            self.sheets_service = SheetsService()
            self.email_service = EmailService()
            self.sms_service = SMSService()
            
            logger.info("All services initialized successfully")
            
        except Exception as error:
            log_error("SERVICE_INITIALIZATION", error)
            raise
    
    def process_new_leads(self, email_only: bool = False, sms_only: bool = False) -> Dict:
        """Process new leads and send initial outreach."""
        logger.info("Starting new lead processing")
        
        try:
            # Create backup before processing
            backup_file = self.sheets_service.create_backup()
            logger.info(f"Backup created: {backup_file}")
            
            # Get new leads
            new_leads = self.sheets_service.get_leads_by_status(config.STATUS_NEW)
            
            if not new_leads:
                logger.info("No new leads found")
                return {"processed": 0, "email_sent": 0, "sms_sent": 0, "errors": 0}
            
            logger.info(f"Found {len(new_leads)} new leads to process")
            
            stats = {"processed": 0, "email_sent": 0, "sms_sent": 0, "errors": 0}
            
            for lead in new_leads:
                try:
                    lead_name = lead.get('name', 'Unknown')
                    lead_email = lead.get('email', '')
                    lead_phone = lead.get('phone', '')
                    
                    logger.info(f"Processing lead: {lead_name}")
                    
                    # Send email if enabled and email available
                    if not sms_only and lead_email:
                        if self.email_service.send_initial_email(lead):
                            stats["email_sent"] += 1
                            self.sheets_service.mark_contacted(lead['row_number'], "Email")
                            logger.info(f"Email sent to {lead_name}")
                        else:
                            logger.warning(f"Failed to send email to {lead_name}")
                            stats["errors"] += 1
                    
                    # Send SMS if enabled and phone available
                    if not email_only and lead_phone:
                        if self.sms_service.send_initial_sms(lead):
                            stats["sms_sent"] += 1
                            # Update status only if email wasn't sent
                            if not lead_email or sms_only:
                                self.sheets_service.mark_contacted(lead['row_number'], "SMS")
                            logger.info(f"SMS sent to {lead_name}")
                        else:
                            logger.warning(f"Failed to send SMS to {lead_name}")
                            stats["errors"] += 1
                    
                    stats["processed"] += 1
                    
                    # Add delay between leads to avoid rate limiting
                    time.sleep(3)
                    
                except Exception as error:
                    log_error("PROCESS_LEAD", error, {"lead": lead.get('name', 'Unknown')})
                    stats["errors"] += 1
            
            log_operation("PROCESS_NEW_LEADS", stats)
            return stats
            
        except Exception as error:
            log_error("PROCESS_NEW_LEADS", error)
            raise
    
    def process_follow_ups(self, email_only: bool = False, sms_only: bool = False) -> Dict:
        """Process leads that need follow-up messages."""
        logger.info("Starting follow-up processing")
        
        try:
            # Get leads that need follow-up
            follow_up_leads = self.sheets_service.get_leads_for_follow_up()
            
            if not follow_up_leads:
                logger.info("No leads need follow-up at this time")
                return {"processed": 0, "email_sent": 0, "sms_sent": 0, "errors": 0}
            
            logger.info(f"Found {len(follow_up_leads)} leads needing follow-up")
            
            stats = {"processed": 0, "email_sent": 0, "sms_sent": 0, "errors": 0}
            
            for lead in follow_up_leads:
                try:
                    lead_name = lead.get('name', 'Unknown')
                    lead_email = lead.get('email', '')
                    lead_phone = lead.get('phone', '')
                    
                    logger.info(f"Processing follow-up for: {lead_name}")
                    
                    # Send follow-up email if enabled and email available
                    if not sms_only and lead_email:
                        if self.email_service.send_follow_up_email(lead):
                            stats["email_sent"] += 1
                            self.sheets_service.mark_follow_up_sent(lead['row_number'], "Email")
                            logger.info(f"Follow-up email sent to {lead_name}")
                        else:
                            logger.warning(f"Failed to send follow-up email to {lead_name}")
                            stats["errors"] += 1
                    
                    # Send follow-up SMS if enabled and phone available
                    if not email_only and lead_phone:
                        if self.sms_service.send_follow_up_sms(lead):
                            stats["sms_sent"] += 1
                            # Update status only if email wasn't sent
                            if not lead_email or sms_only:
                                self.sheets_service.mark_follow_up_sent(lead['row_number'], "SMS")
                            logger.info(f"Follow-up SMS sent to {lead_name}")
                        else:
                            logger.warning(f"Failed to send follow-up SMS to {lead_name}")
                            stats["errors"] += 1
                    
                    stats["processed"] += 1
                    
                    # Add delay between leads
                    time.sleep(3)
                    
                except Exception as error:
                    log_error("PROCESS_FOLLOW_UP", error, {"lead": lead.get('name', 'Unknown')})
                    stats["errors"] += 1
            
            log_operation("PROCESS_FOLLOW_UPS", stats)
            return stats
            
        except Exception as error:
            log_error("PROCESS_FOLLOW_UPS", error)
            raise
    
    def check_responses(self) -> Dict:
        """Check for email and SMS responses."""
        logger.info("Checking for responses")
        
        try:
            # Check email replies
            email_replies = self.email_service.check_replies()
            sms_replies = self.sms_service.check_replies()
            
            # Process unsubscribes
            for reply in email_replies + sms_replies:
                if reply['type'] == 'unsubscribe' or reply['type'] == 'opt_out':
                    # Find lead by email/phone and mark as unsubscribed
                    self._process_unsubscribe(reply)
            
            stats = {
                "email_replies": len(email_replies),
                "sms_replies": len(sms_replies),
                "unsubscribes": len([r for r in email_replies + sms_replies 
                                   if r['type'] in ['unsubscribe', 'opt_out']])
            }
            
            log_operation("CHECK_RESPONSES", stats)
            return stats
            
        except Exception as error:
            log_error("CHECK_RESPONSES", error)
            return {"email_replies": 0, "sms_replies": 0, "unsubscribes": 0}
    
    def _process_unsubscribe(self, reply: Dict):
        """Process an unsubscribe request."""
        try:
            # Get all leads to find the matching one
            all_leads = self.sheets_service.get_all_leads()
            
            contact_info = reply.get('from', '')
            
            for lead in all_leads:
                if (lead.get('email') == contact_info or 
                    lead.get('phone') in contact_info or 
                    contact_info in lead.get('phone', '')):
                    
                    self.sheets_service.mark_unsubscribed(
                        lead['row_number'], 
                        f"Via {reply['type']}"
                    )
                    logger.info(f"Marked {lead.get('name')} as unsubscribed")
                    break
                    
        except Exception as error:
            log_error("PROCESS_UNSUBSCRIBE", error, {"reply": reply})
    
    def get_system_status(self) -> Dict:
        """Get current system status and statistics."""
        try:
            all_leads = self.sheets_service.get_all_leads()
            
            # Count leads by status
            status_counts = {}
            for lead in all_leads:
                status = lead.get('status', 'Unknown')
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Get service stats
            email_stats = self.email_service.get_email_stats()
            sms_stats = self.sms_service.get_sms_stats()
            
            status = {
                "timestamp": datetime.now().isoformat(),
                "total_leads": len(all_leads),
                "status_breakdown": status_counts,
                "email_service": email_stats,
                "sms_service": sms_stats,
                "follow_ups_pending": len(self.sheets_service.get_leads_for_follow_up())
            }
            
            return status
            
        except Exception as error:
            log_error("GET_SYSTEM_STATUS", error)
            return {"error": str(error)}

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Cold Outreach Automation System")
    parser.add_argument("--mode", choices=["new", "follow-up", "both", "status", "check-responses"], 
                       default="both", help="Operation mode")
    parser.add_argument("--email-only", action="store_true", 
                       help="Send emails only")
    parser.add_argument("--sms-only", action="store_true", 
                       help="Send SMS only")
    parser.add_argument("--dry-run", action="store_true", 
                       help="Preview what would be done without actually sending")
    
    args = parser.parse_args()
    
    try:
        automation = OutreachAutomation()
        
        if args.mode == "status":
            status = automation.get_system_status()
            print("\n=== SYSTEM STATUS ===")
            print(f"Total Leads: {status.get('total_leads', 0)}")
            print(f"Follow-ups Pending: {status.get('follow_ups_pending', 0)}")
            print("\nStatus Breakdown:")
            for status_name, count in status.get('status_breakdown', {}).items():
                print(f"  {status_name}: {count}")
            print(f"\nEmail Service: {status.get('email_service', {}).get('sent_this_hour', 0)}/{status.get('email_service', {}).get('rate_limit', 0)} sent this hour")
            print(f"SMS Service: {status.get('sms_service', {}).get('sent_this_hour', 0)}/{status.get('sms_service', {}).get('rate_limit', 0)} sent this hour")
            
        elif args.mode == "check-responses":
            stats = automation.check_responses()
            print(f"\n=== RESPONSE CHECK ===")
            print(f"Email Replies: {stats['email_replies']}")
            print(f"SMS Replies: {stats['sms_replies']}")
            print(f"Unsubscribes: {stats['unsubscribes']}")
            
        elif args.mode in ["new", "both"]:
            if args.dry_run:
                new_leads = automation.sheets_service.get_leads_by_status(config.STATUS_NEW)
                print(f"Would process {len(new_leads)} new leads")
            else:
                stats = automation.process_new_leads(args.email_only, args.sms_only)
                print(f"\n=== NEW LEADS PROCESSED ===")
                print(f"Processed: {stats['processed']}")
                print(f"Emails Sent: {stats['email_sent']}")
                print(f"SMS Sent: {stats['sms_sent']}")
                print(f"Errors: {stats['errors']}")
        
        if args.mode in ["follow-up", "both"]:
            if args.dry_run:
                follow_up_leads = automation.sheets_service.get_leads_for_follow_up()
                print(f"Would process {len(follow_up_leads)} follow-up leads")
            else:
                stats = automation.process_follow_ups(args.email_only, args.sms_only)
                print(f"\n=== FOLLOW-UPS PROCESSED ===")
                print(f"Processed: {stats['processed']}")
                print(f"Emails Sent: {stats['email_sent']}")
                print(f"SMS Sent: {stats['sms_sent']}")
                print(f"Errors: {stats['errors']}")
        
        logger.info("Automation run completed successfully")
        
    except KeyboardInterrupt:
        logger.info("Automation interrupted by user")
        sys.exit(0)
    except Exception as error:
        log_error("MAIN_EXECUTION", error)
        print(f"Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    main() 